RSpec.describe Namespace::ServiceName do
  subject(:service) { described_class.new(record, notifier: notifier) }

  let(:record) { Struct.new(:state).new(state) }
  let(:state) { :eligible }
  let(:notifier) { instance_double(Notifier) }

  before { allow(notifier).to receive(:call) }

  describe '#call' do
    subject(:result) { service.call }

    context 'when the record is eligible' do
      it { is_expected.to be_success }

      it 'changes the record state' do
        expect { result }.to change(record, :state).to(:done)
      end

      it 'notifies the boundary once' do
        result

        expect(notifier).to have_received(:call).with(record).once
      end
    end

    context 'when the record is not eligible' do
      let(:state) { :ineligible }

      it { is_expected.to be_failure }

      it 'leaves the record state alone' do
        expect { result }.not_to change(record, :state)
      end

      it 'does not notify the boundary' do
        result

        expect(notifier).not_to have_received(:call)
      end
    end
  end
end
